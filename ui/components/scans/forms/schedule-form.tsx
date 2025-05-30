"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Dispatch, SetStateAction } from "react";
import { useForm } from "react-hook-form";
import * as z from "zod";

import { updateProvider } from "@/actions/providers";
import { SaveIcon } from "@/components/icons";
import { useToast } from "@/components/ui";
import { CustomButton, CustomInput } from "@/components/ui/custom";
import { Form } from "@/components/ui/form";
import { scheduleScanFormSchema } from "@/types";

export const ScheduleForm = ({
  providerId,
  scheduleDate,
  setIsOpen,
}: {
  providerId: string;
  scheduleDate: string;
  setIsOpen: Dispatch<SetStateAction<boolean>>;
}) => {
  const formSchema = scheduleScanFormSchema();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      providerId: providerId,
      scheduleDate: scheduleDate,
    },
  });

  const { toast } = useToast();

  const isLoading = form.formState.isSubmitting;

  const onSubmitClient = async (values: z.infer<typeof formSchema>) => {
    const formData = new FormData();

    Object.entries(values).forEach(
      ([key, value]) => value !== undefined && formData.append(key, value),
    );
    const data = await updateProvider(formData);

    if (data?.errors && data.errors.length > 0) {
      const error = data.errors[0];
      const errorMessage = `${error.detail}`;
      // show error
      toast({
        variant: "destructive",
        title: "Oops! Something went wrong",
        description: errorMessage,
      });
    } else {
      toast({
        title: "Success!",
        description: "The scan was scheduled successfully.",
      });
      setIsOpen(false); // Close the modal on success
    }
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmitClient)}
        className="flex flex-col space-y-4"
      >
        <input type="hidden" name="providerId" value={providerId} />
        <CustomInput
          control={form.control}
          name="scheduleDate"
          type="date"
          label="Schedule Date"
          labelPlacement="inside"
          variant="bordered"
          isRequired={false}
          isInvalid={!!form.formState.errors.scheduleDate}
        />

        <div className="flex w-full justify-center sm:space-x-6">
          <CustomButton
            type="button"
            ariaLabel="Cancel"
            className="w-full bg-transparent"
            variant="faded"
            size="lg"
            radius="lg"
            onPress={() => setIsOpen(false)}
            isDisabled={isLoading}
          >
            <span>Cancel</span>
          </CustomButton>

          <CustomButton
            type="submit"
            ariaLabel="Schedule scan"
            className="w-full"
            variant="solid"
            color="action"
            size="lg"
            isLoading={isLoading}
            startContent={!isLoading && <SaveIcon size={24} />}
            isDisabled={true}
          >
            {isLoading ? <>Loading</> : <span>Schedule</span>}
          </CustomButton>
        </div>
      </form>
    </Form>
  );
};
